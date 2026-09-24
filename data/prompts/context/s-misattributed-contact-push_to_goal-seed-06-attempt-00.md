## Search State

- **Seed**: 6
- **Iteration**: 1 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 0 | align → lift → push → approach → approach → descend → grasp | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | -0.0821 | 0.00 | ✅ accepted |

**Proposal policy**: task_score is 0.00 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
- task_score stagnant: change coupled targets, parameters, terminations, phase types, controls, subtasks, or ordering when evidence shows they need to change together.
A HOLD wastes an iteration when task_score is below 0.9.

## Optimisation Objective

Your goal is to **maximise task_score first, then composite score Q**:

> **Primary objective: task_score** — the fraction of episodes where the robot successfully completes the task. This is the most important metric. **Never propose a simpler or shorter skill if it reduces task_score.**

> **Q = fitness_score + termination_fidelity − complexity_penalty**

- `fitness_score`: shaped task reward (includes phase progress for contact-rich tasks)
- `termination_fidelity`: fraction of phases that terminated by designed condition (not timeout)
- `complexity_penalty`: cost for over-parameterised or over-phased designs

**Warning**: Do not reduce phases or parameters to lower complexity if doing so reduces task_score. Structure complexity is only penalised when it adds no performance gain.

# Proposal Context

## Task Specification

- Task name: push_to_goal
- Frozen realised-scene SHA-256: `5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7`
- Frozen object start: [0.5045797221766332, -0.01880749562239939, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.5045797221766332, -0.01880749562239939, 0.025)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.8
- Force limit: 25.0 N
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **object displacement ratio toward goal_object_position**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: push_box
    role: manipulated_object
    dynamics: free
    geometry: box
    dimensions_m: [0.05, 0.05, 0.05]
    mass_kg: 0.1
  - name: goal_marker
    role: target_marker
    dynamics: static
    geometry: point
task_landmarks:
  frozen_object_start: [0.5046, -0.0188, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.5045797221766332, -0.01880749562239939, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.0046, -0.1312, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7

## Subtask Layer

**Mode**: free (you define subtask targets; use `subtasks:` block in your YAML)

Define subtasks in a `subtasks:` block **before** `phases:`. Each subtask specifies an intermediate optimisation target.

**Required fields** — always include both, never omit:
- `anchor` (**required**): fixture | goal | object | world
- `target_entity` (**required**): hinge | object | tcp

Subtask anchors are separate from phase `target.anchor` vocabulary: subtasks use `world | object | goal | fixture`, while phase targets use `world | task_goal | task_object | fixture | body | site | current_tcp`.

Optional fields:
- `metric`: contact | distance | goal_progress | hinge_angle (default: distance)
- `offset`: [x, y, z] in metres relative to anchor (default: [0, 0, 0])
- `param_offset_key`: CMA-ES parameter added to offset at runtime (optional)
- `weight`: scoring weight [0.1, 1.0] (default: 1.0)

**Anchor resolution for this task** — choose anchor so the resolved position is meaningful:
| Anchor | Resolves to | Best used for |
|--------|-------------|---------------|
| `world` | absolute world-frame coordinate | fixed reference points not tied to objects |
| `object` | offset from object initial position (0.5045797221766332, -0.01880749562239939, 0.025) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, -0.15, 0.025) | final destination targets |
| `fixture` | offset from fixture pose (if defined, else world) | targets near fixture |

Annotate each phase with `subtask_id: <id>` to bind it to a subtask.
Only the **last phase** bound to a given subtask contributes to subtask scoring.

Example (two subtasks — one near object start, one at goal):
```yaml
subtasks:
  - id: reach_pre_contact
    anchor: object         # resolved to object initial position (see table above)
    target_entity: tcp     # score TCP distance to this target
    metric: distance
    offset: [0.0, 0.0, 0.10]  # 10 cm above object start position
    weight: 0.3
  - id: reach_goal
    anchor: goal           # resolved to task goal position (see table above)
    target_entity: tcp
    metric: distance
    offset: [0.0, 0.0, 0.0]
    weight: 0.7
phases:
  - id: approach_1
    type: approach
    subtask_id: reach_pre_contact
    ...
  - id: push_1
    type: push
    subtask_id: reach_goal
    ...
```

## Current Skill (Q=-0.082) — your mutation base

```yaml
skill: push_to_goal
skill_type: arm_gripper
phases:
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    lateral_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.3
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
- id: approach_2
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
- id: grasp_1
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp

```

## Design Metrics

- **Composite score**: -0.082
- **task_score** (E): 0.000
- **fitness_score**: 0.318  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.400

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 1.00 | 0.2901 |
| lift_1 | 0.00 | 1.00 | 0.1699 |
| push_1 | 1.00 | 1.00 | 0.1931 |
| approach_1 | 0.33 | 1.00 | 0.1750 |
| approach_2 | 1.00 | 1.00 | 0.1051 |
| descend_1 | 0.00 | 1.00 | 0.1901 |
| grasp_1 | 1.00 | 1.00 | 0.0107 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.104, 0.032) | (0.500, 0.029, 0.025)→(0.500, 0.029, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| lift_1 | lift | 0.00 / step_budget | (0.496, 0.104, 0.032)→(0.435, 0.003, 0.154) | (0.500, 0.029, 0.025)→(0.500, 0.029, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| push_1 | push | 1.00 / step_budget | (0.435, 0.003, 0.154)→(0.493, -0.127, 0.026) | (0.500, 0.029, 0.025)→(0.500, 0.029, 0.025) | 0.180→0.180 | 1.00 / 2.000 | 31.358 | 64.038 |
| approach_1 | approach | 0.33 / step_budget | (0.493, -0.127, 0.026)→(0.496, 0.047, 0.039) | (0.500, 0.029, 0.025)→(0.510, 0.079, 0.028) | 0.180→0.231 | 1.00 / 3.667 | 40.723 | 72.061 |
| approach_2 | approach | 1.00 / step_budget | (0.496, 0.047, 0.039)→(0.507, 0.150, 0.028) | (0.510, 0.079, 0.028)→(0.538, 0.155, 0.030) | 0.231→0.309 | 1.00 / 4.000 | 0.245 | 75.358 |
| descend_1 | descend | 0.00 / step_budget | (0.507, 0.150, 0.028)→(0.498, -0.039, 0.021) | (0.538, 0.155, 0.030)→(0.513, 0.102, 0.025) | 0.309→0.252 | 1.00 / 4.000 | 0.245 | 0.245 |
| grasp_1 | grasp | 1.00 / step_budget | (0.498, -0.039, 0.021)→(0.491, -0.039, 0.013) | (0.513, 0.102, 0.025)→(0.513, 0.102, 0.025) | 0.252→0.252 | 1.00 / 4.000 | 0.245 | 0.245 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.343
- lateral_force_integral: None
- approach_alignment: 0.576
- goal_progress: 0.000
- terminal_score: 0.000
- phase_score: 0.573
- phase_breakdown.approach_score: 0.684
- phase_breakdown.contact_score: 0.000
- phase_breakdown.push_score: 0.872

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.344
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: -0.068
- **K-run variance**: 0.0008
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.328


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `acf3715aaa310bcc73047d49f01e71bc863ef036ae437b7dc851a0f6d3fe40ae`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `ec1d0331416d42e6883eeb3b72499fac99c0735b785eb70ece69dc94e8044fc3`; realized-scene SHA-256: `5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50458,-0.01881,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.00458,-0.13119,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.50458,-0.01881,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.32286,"average_solve_count":350.0,"average_success_count":350.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":-0.00087,"approach_2.speed":0.02538,"lift_1.lift_height":0.19881,"push_1.push_distance":0.11376,"push_1.push_speed":0.04185},"optimized_scores":{"best_composite_score":-0.12199,"best_fitness_score":0.27801,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":2480.0,"contact_point_centroid":[0.51253,0.00393,-6e-05],"force_p95":41.83847,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":130.2112,"mean_force":7.09859,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49337,-0.0594,0.03389]},{"body_a":"attachment","body_b":"push_box","contact_count":498.0,"contact_point_centroid":[0.50999,0.007,0.05096],"force_p95":81.27642,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":120.06952,"mean_force":22.53684,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49746,-0.00285,0.03628]},{"body_a":"push_box","body_b":"link7","contact_count":166.0,"contact_point_centroid":[0.53753,0.03648,0.05981],"force_p95":93.94504,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":116.25904,"mean_force":55.69399,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50151,0.0326,0.03181]},{"body_a":"world","body_b":"push_box","contact_count":1837.0,"contact_point_centroid":[0.55508,0.06351,-0.0003],"force_p95":87.0139,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":95.64856,"mean_force":28.01124,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51537,0.04773,0.02563]},{"body_a":"push_box","body_b":"link7","contact_count":797.0,"contact_point_centroid":[0.55895,0.08382,0.05506],"force_p95":87.84858,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":95.47559,"mean_force":57.48967,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51879,0.07543,0.02739]},{"body_a":"push_box","body_b":"link7","contact_count":261.0,"contact_point_centroid":[0.54746,0.07345,0.06021],"force_p95":57.99217,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":83.34151,"mean_force":25.10578,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.51038,0.07212,0.03216]},{"body_a":"attachment","body_b":"push_box","contact_count":719.0,"contact_point_centroid":[0.53273,0.09184,0.05052],"force_p95":49.13565,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":74.2294,"mean_force":9.84731,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.51343,0.08998,0.03401]},{"body_a":"world","body_b":"push_box","contact_count":1360.0,"contact_point_centroid":[0.56309,0.10262,-9e-05],"force_p95":26.49373,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":72.1413,"mean_force":7.55524,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.51369,0.09134,0.03413]},{"body_a":"attachment","body_b":"push_box","contact_count":457.0,"contact_point_centroid":[0.54616,0.10739,0.06114],"force_p95":45.79541,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":50.35151,"mean_force":33.23105,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52151,0.10642,0.02854]},{"body_a":"world","body_b":"push_box","contact_count":3492.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49925,0.02864,0.16605]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46549,0.01415,0.09528]},{"body_a":"world","body_b":"push_box","contact_count":3348.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46272,-0.07793,0.09181]},{"body_a":"world","body_b":"push_box","contact_count":1800.0,"contact_point_centroid":[0.51463,0.04271,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":6.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49957,-0.03824,0.01465]}],"total_contact_groups":13},"final_pose_error":0.11199,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51463,0.04271,0.02499],"final_tcp_position":[0.50571,-0.03821,0.02154],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":130.2112,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":873.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.50028,0.0578,0.03311],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07716,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3348.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.4348,-0.02857,0.16105],"tcp_start":[0.50028,0.0578,0.03311],"tcp_to_object_dist_end":0.15322,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":837.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"peak_contact_force":93.943,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3144.0,"raw_peak_contact_force":130.2112,"tcp_end":[0.49246,-0.12637,0.02708],"tcp_start":[0.4348,-0.02857,0.16105],"tcp_to_object_dist_end":0.10826,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53173,0.07094,0.03148],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.2233,"object_to_goal_dist_start":0.13127,"object_z_max":0.03164,"peak_contact_force":16.74804,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2340.0,"raw_peak_contact_force":83.34151,"tcp_end":[0.50502,0.04405,0.03012],"tcp_start":[0.49246,-0.12637,0.02708],"tcp_to_object_dist_end":0.03793,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":873.0,"n_steps_budget":1000.0,"object_pos_end":[0.5631,0.11985,0.03263],"object_pos_start":[0.53173,0.07094,0.03148],"object_to_goal_dist_end":0.27723,"object_to_goal_dist_start":0.2233,"object_z_max":0.03288,"peak_contact_force":0.24525,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3091.0,"raw_peak_contact_force":95.64856,"tcp_end":[0.52622,0.14294,0.02916],"tcp_start":[0.50502,0.04405,0.03012],"tcp_to_object_dist_end":0.04365,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51463,0.04271,0.02499],"object_pos_start":[0.5631,0.11985,0.03263],"object_to_goal_dist_end":0.19327,"object_to_goal_dist_start":0.27723,"object_z_max":0.03489,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1800.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.50571,-0.03821,0.02154],"tcp_start":[0.52622,0.14294,0.02916],"tcp_to_object_dist_end":0.08148,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51463,0.04271,0.02499],"object_pos_start":[0.51463,0.04271,0.02499],"object_to_goal_dist_end":0.19327,"object_to_goal_dist_start":0.19327,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3492.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.49846,-0.03818,0.01341],"tcp_start":[0.50571,-0.03821,0.02154],"tcp_to_object_dist_end":0.0833,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `589e611c6c27578474525e3fd29be4fb5907d8bbd5d1ca44922bfd811e342c78`; realized-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51501,0.04767,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.01501,-0.19767,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.51501,0.04767,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.74912,"average_solve_count":283.0,"average_success_count":283.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":-0.0046,"approach_2.speed":0.06156,"lift_1.lift_height":0.11189,"push_1.push_distance":0.182,"push_1.push_speed":0.06271},"optimized_scores":{"best_composite_score":-0.05624,"best_fitness_score":0.34376,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":145.0,"contact_point_centroid":[0.54817,0.11325,0.06326],"force_p95":75.22116,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":94.864,"mean_force":43.22632,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.51628,0.13537,0.03248]},{"body_a":"world","body_b":"push_box","contact_count":2608.0,"contact_point_centroid":[0.53752,0.11272,-0.00014],"force_p95":70.96207,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":85.46807,"mean_force":9.77804,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50816,0.02627,0.0236]},{"body_a":"world","body_b":"push_box","contact_count":1076.0,"contact_point_centroid":[0.55264,0.12519,-0.00014],"force_p95":54.92301,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":84.74724,"mean_force":13.13639,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.50943,0.09757,0.0388]},{"body_a":"push_box","body_b":"link7","contact_count":442.0,"contact_point_centroid":[0.55451,0.12061,0.05596],"force_p95":75.17317,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":82.96422,"mean_force":52.8397,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51569,0.10801,0.02785]},{"body_a":"attachment","body_b":"push_box","contact_count":576.0,"contact_point_centroid":[0.52503,0.10394,0.05475],"force_p95":49.33734,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":75.7692,"mean_force":13.72843,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.50926,0.09665,0.03889]},{"body_a":"attachment","body_b":"push_box","contact_count":266.0,"contact_point_centroid":[0.54128,0.12778,0.06037],"force_p95":42.92282,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.22316,"mean_force":29.74122,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51687,0.12412,0.02858]},{"body_a":"attachment","body_b":"push_box","contact_count":147.0,"contact_point_centroid":[0.50691,0.03821,0.04999],"force_p95":21.53413,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.11595,"mean_force":9.17776,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5026,0.0264,0.0444]},{"body_a":"world","body_b":"push_box","contact_count":3487.0,"contact_point_centroid":[0.5156,0.05025,-1e-05],"force_p95":2.20989,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.26945,"mean_force":0.65075,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49583,-0.05263,0.03855]},{"body_a":"world","body_b":"push_box","contact_count":3960.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50423,0.06072,0.1639]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47617,0.06905,0.08765]},{"body_a":"world","body_b":"push_box","contact_count":3684.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46897,-0.05595,0.08415]},{"body_a":"world","body_b":"push_box","contact_count":1800.0,"contact_point_centroid":[0.5291,0.11417,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":6.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49672,-0.04344,0.01486]}],"total_contact_groups":12},"final_pose_error":0.10659,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5291,0.11417,0.02499],"final_tcp_position":[0.50283,-0.0435,0.02168],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":94.864,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":990.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.51027,0.12151,0.03099],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07424,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3684.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.44615,0.01783,0.14851],"tcp_start":[0.51027,0.12151,0.03099],"tcp_to_object_dist_end":0.14453,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":921.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":0.07164,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3634.0,"raw_peak_contact_force":27.11595,"tcp_end":[0.49345,-0.12686,0.02539],"tcp_start":[0.44615,0.01783,0.14851],"tcp_to_object_dist_end":0.17585,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52119,0.07494,0.02746],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.22595,"object_to_goal_dist_start":0.19823,"object_z_max":0.02746,"peak_contact_force":67.65014,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1797.0,"raw_peak_contact_force":94.864,"tcp_end":[0.50413,0.04242,0.04293],"tcp_start":[0.49345,-0.12686,0.02539],"tcp_to_object_dist_end":0.03986,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":716.0,"n_steps_budget":1000.0,"object_pos_end":[0.55947,0.1454,0.03122],"object_pos_start":[0.52119,0.07494,0.02746],"object_to_goal_dist_end":0.30139,"object_to_goal_dist_start":0.22595,"object_z_max":0.03214,"peak_contact_force":0.24525,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3316.0,"raw_peak_contact_force":85.46807,"tcp_end":[0.51983,0.14544,0.02978],"tcp_start":[0.50413,0.04242,0.04293],"tcp_to_object_dist_end":0.03966,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5291,0.11417,0.02499],"object_pos_start":[0.55947,0.1454,0.03122],"object_to_goal_dist_end":0.26576,"object_to_goal_dist_start":0.30139,"object_z_max":0.03331,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1800.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.50283,-0.0435,0.02168],"tcp_start":[0.51983,0.14544,0.02978],"tcp_to_object_dist_end":0.15987,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5291,0.11417,0.02499],"object_pos_start":[0.5291,0.11417,0.02499],"object_to_goal_dist_end":0.26576,"object_to_goal_dist_start":0.26576,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3960.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.49561,-0.04338,0.01363],"tcp_start":[0.50283,-0.0435,0.02168],"tcp_to_object_dist_end":0.16146,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f2c9c63f0d9eca1b3ff8bf951759f6a3adee73f9f65e1cd3613c5e9d1203ebcc`; realized-scene SHA-256: `f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47924,0.05847,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02076,-0.20847,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47924,0.05847,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92832,"average_solve_count":279.0,"average_success_count":279.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":-0.00826,"approach_2.speed":0.07439,"lift_1.lift_height":0.29931,"push_1.push_distance":0.19296,"push_1.push_speed":0.07151},"optimized_scores":{"best_composite_score":-0.0681,"best_fitness_score":0.3319,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":234.0,"contact_point_centroid":[0.51213,0.16565,0.05584],"force_p95":43.79236,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.9569,"mean_force":17.73431,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47535,0.13281,0.02238]},{"body_a":"world","body_b":"push_box","contact_count":3232.0,"contact_point_centroid":[0.49391,0.15281,-5e-05],"force_p95":6.67516,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.0883,"mean_force":1.58929,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48064,0.04301,0.02056]},{"body_a":"attachment","body_b":"push_box","contact_count":460.0,"contact_point_centroid":[0.47948,0.12123,0.04642],"force_p95":31.35058,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.9765,"mean_force":9.83245,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.47562,0.10918,0.03895]},{"body_a":"push_box","body_b":"link7","contact_count":17.0,"contact_point_centroid":[0.51663,0.17344,0.04978],"force_p95":37.38184,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.77221,"mean_force":22.09569,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.47474,0.1603,0.02572]},{"body_a":"world","body_b":"push_box","contact_count":953.0,"contact_point_centroid":[0.48313,0.1593,-0.00011],"force_p95":17.60685,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":35.46097,"mean_force":5.54338,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.47573,0.10739,0.03894]},{"body_a":"attachment","body_b":"push_box","contact_count":135.0,"contact_point_centroid":[0.48039,0.04994,0.04546],"force_p95":29.87739,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.78629,"mean_force":9.97273,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48059,0.03807,0.04517]},{"body_a":"world","body_b":"push_box","contact_count":3548.0,"contact_point_centroid":[0.47929,0.06089,-1e-05],"force_p95":1.05913,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.7604,"mean_force":0.63653,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4849,-0.04736,0.03933]},{"body_a":"attachment","body_b":"push_box","contact_count":48.0,"contact_point_centroid":[0.48745,0.1695,0.04908],"force_p95":5.24117,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.32325,"mean_force":3.17715,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47507,0.15711,0.0244]},{"body_a":"world","body_b":"push_box","contact_count":3972.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48715,0.06586,0.16416]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44808,0.07594,0.09006]},{"body_a":"world","body_b":"push_box","contact_count":3932.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.45781,-0.05516,0.08598]},{"body_a":"world","body_b":"push_box","contact_count":1800.0,"contact_point_centroid":[0.49379,0.14815,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":6.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48063,-0.03556,0.01381]}],"total_contact_groups":12},"final_pose_error":0.11539,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49379,0.14815,0.02499],"final_tcp_position":[0.48663,-0.03548,0.02023],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":44.9569,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":993.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.47614,0.13178,0.03157],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07366,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3932.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.42362,0.02089,0.15291],"tcp_start":[0.47614,0.13178,0.03157],"tcp_to_object_dist_end":0.14446,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":983.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":0.05889,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3683.0,"raw_peak_contact_force":34.78629,"tcp_end":[0.4928,-0.1276,0.025],"tcp_start":[0.42362,0.02089,0.15291],"tcp_to_object_dist_end":0.18657,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47806,0.09146,0.02542],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.24245,"object_to_goal_dist_start":0.2095,"object_z_max":0.02577,"peak_contact_force":37.77221,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1430.0,"raw_peak_contact_force":37.9765,"tcp_end":[0.47984,0.05464,0.04332],"tcp_start":[0.4928,-0.1276,0.025],"tcp_to_object_dist_end":0.04098,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":639.0,"n_steps_budget":990.0,"object_pos_end":[0.49114,0.19896,0.02491],"object_pos_start":[0.47806,0.09146,0.02542],"object_to_goal_dist_end":0.34907,"object_to_goal_dist_start":0.24245,"object_z_max":0.02708,"peak_contact_force":0.24525,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3514.0,"raw_peak_contact_force":44.9569,"tcp_end":[0.47504,0.16196,0.02495],"tcp_start":[0.47984,0.05464,0.04332],"tcp_to_object_dist_end":0.04035,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49379,0.14815,0.02499],"object_pos_start":[0.49114,0.19896,0.02491],"object_to_goal_dist_end":0.29822,"object_to_goal_dist_start":0.34907,"object_z_max":0.03528,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1800.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.48663,-0.03548,0.02023],"tcp_start":[0.47504,0.16196,0.02495],"tcp_to_object_dist_end":0.18383,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49379,0.14815,0.02499],"object_pos_start":[0.49379,0.14815,0.02499],"object_to_goal_dist_end":0.29822,"object_to_goal_dist_start":0.29822,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3972.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.47954,-0.0355,0.01264],"tcp_start":[0.48663,-0.03548,0.02023],"tcp_to_object_dist_end":0.18462,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```