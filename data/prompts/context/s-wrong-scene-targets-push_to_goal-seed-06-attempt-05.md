## Search State

- **Seed**: 6
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | align → lift → push → approach → approach → descend → grasp | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | -0.0837 | 0.00 | ❌ rejected |
| 4 | align → lift → push → approach → approach → descend → grasp | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | -0.0827 | 0.00 | ❌ rejected |
| 3 | align → lift → push → approach → approach → descend → grasp | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | -0.0849 | 0.00 | ❌ rejected |
| 2 | align → lift → push → approach → approach → descend → grasp | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | -0.0821 | 0.00 | ✅ accepted |
| 1 | align → lift → push → approach → approach → descend → grasp | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | -0.0824 | 0.00 | ❌ rejected |

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
- Frozen object start: [0.5, -0.15, 0.025]
- Frozen task target: [0.5, 0.0, 0.3]
- Goal object position: (0.5, 0.0, 0.3)
- Object initial pose: (0.5, -0.15, 0.025)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.8
- Force limit: 25.0 N
- Robot initial TCP position: (0.5045797221766332, -0.01880749562239939, 0.025)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **object displacement ratio toward goal_object_position**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5045797221766332, -0.01880749562239939, 0.025]
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
  frozen_task_target: [0.5, 0.0, 0.3]
  frozen_object_starts: {'push_box': [0.5, -0.15, 0.025]}
  frozen_targets: {'task_goal': [0.5, 0.0, 0.3]}
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
| `object` | offset from object initial position (0.5, -0.15, 0.025) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, 0.0, 0.3) | final destination targets |
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

## Current Skill (Q=-0.084) — your mutation base

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

- **Composite score**: -0.084
- **task_score** (E): 0.000
- **fitness_score**: 0.316  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.400

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 1.00 | 0.2901 |
| lift_1 | 0.00 | 1.00 | 0.1699 |
| push_1 | 1.00 | 1.00 | 0.1918 |
| approach_1 | 0.33 | 1.00 | 0.1750 |
| approach_2 | 1.00 | 1.00 | 0.1052 |
| descend_1 | 0.00 | 1.00 | 0.1878 |
| grasp_1 | 1.00 | 1.00 | 0.0107 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.104, 0.032) | (0.500, 0.029, 0.025)→(0.500, 0.029, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| lift_1 | lift | 0.00 / step_budget | (0.496, 0.104, 0.032)→(0.435, 0.003, 0.154) | (0.500, 0.029, 0.025)→(0.500, 0.029, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| push_1 | push | 1.00 / step_budget | (0.435, 0.003, 0.154)→(0.493, -0.125, 0.026) | (0.500, 0.029, 0.025)→(0.500, 0.029, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| approach_1 | approach | 0.33 / step_budget | (0.493, -0.125, 0.026)→(0.497, 0.049, 0.039) | (0.500, 0.029, 0.025)→(0.510, 0.081, 0.028) | 0.180→0.233 | 1.00 / 2.000 | 40.022 | 73.024 |
| approach_2 | approach | 1.00 / step_budget | (0.497, 0.049, 0.039)→(0.506, 0.152, 0.028) | (0.510, 0.081, 0.028)→(0.517, 0.151, 0.029) | 0.233→0.308 | 1.00 / 3.667 | 32.235 | 67.021 |
| descend_1 | descend | 0.00 / step_budget | (0.506, 0.152, 0.028)→(0.498, -0.035, 0.021) | (0.517, 0.151, 0.029)→(0.489, 0.114, 0.025) | 0.308→0.267 | 1.00 / 4.000 | 0.245 | 59.837 |
| grasp_1 | grasp | 1.00 / step_budget | (0.498, -0.035, 0.021)→(0.491, -0.035, 0.013) | (0.489, 0.114, 0.025)→(0.489, 0.114, 0.025) | 0.267→0.267 | 1.00 / 4.000 | 0.245 | 0.245 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.275
- lateral_force_integral: None
- approach_alignment: 0.573
- goal_progress: 0.000
- terminal_score: 0.000
- phase_score: 0.569
- phase_breakdown.contact_score: 0.000
- phase_breakdown.push_score: 0.874
- phase_breakdown.approach_score: 0.657

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.341
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: -0.070
- **K-run variance**: 0.0008
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.307


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
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.50458,-0.01881,0.025]}],"axes":[{"name":"push_direction","value":[-0.00458,-0.13119,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.50458,-0.01881,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.28571,"average_solve_count":385.0,"average_success_count":385.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":0.00094,"approach_2.speed":0.02472,"lift_1.lift_height":0.18068,"push_1.push_distance":0.11326,"push_1.push_speed":0.02789},"optimized_scores":{"best_composite_score":-0.12213,"best_fitness_score":0.27787,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":172.0,"contact_point_centroid":[0.54092,0.03967,0.05801],"force_p95":90.01862,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":141.97757,"mean_force":50.42436,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50147,0.03282,0.03173]},{"body_a":"attachment","body_b":"push_box","contact_count":483.0,"contact_point_centroid":[0.51026,0.00838,0.05178],"force_p95":71.093,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":119.74511,"mean_force":20.35031,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49755,-0.00169,0.03607]},{"body_a":"world","body_b":"push_box","contact_count":2442.0,"contact_point_centroid":[0.51253,0.00373,-7e-05],"force_p95":46.80932,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":114.86055,"mean_force":6.86657,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49333,-0.05992,0.03379]},{"body_a":"world","body_b":"push_box","contact_count":1660.0,"contact_point_centroid":[0.55849,0.07199,-0.00033],"force_p95":85.44752,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":93.84884,"mean_force":30.88442,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51537,0.05204,0.02558]},{"body_a":"push_box","body_b":"link7","contact_count":826.0,"contact_point_centroid":[0.55837,0.08838,0.05482],"force_p95":84.79147,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":91.53606,"mean_force":56.1106,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51846,0.07825,0.0271]},{"body_a":"push_box","body_b":"link7","contact_count":270.0,"contact_point_centroid":[0.54552,0.07728,0.06108],"force_p95":60.86958,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":89.95841,"mean_force":24.41524,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.51084,0.07409,0.03195]},{"body_a":"attachment","body_b":"push_box","contact_count":753.0,"contact_point_centroid":[0.53156,0.09356,0.04773],"force_p95":44.04714,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":72.56208,"mean_force":8.95843,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.51352,0.09117,0.03399]},{"body_a":"world","body_b":"push_box","contact_count":1367.0,"contact_point_centroid":[0.56187,0.10673,-7e-05],"force_p95":25.75913,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":61.08217,"mean_force":7.29993,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.51363,0.09168,0.03404]},{"body_a":"attachment","body_b":"push_box","contact_count":463.0,"contact_point_centroid":[0.54512,0.10887,0.06023],"force_p95":45.52427,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.09292,"mean_force":31.10348,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52092,0.10714,0.02805]},{"body_a":"world","body_b":"push_box","contact_count":3492.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49925,0.02864,0.16605]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46549,0.01415,0.09528]},{"body_a":"world","body_b":"push_box","contact_count":3376.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46271,-0.07769,0.09181]},{"body_a":"world","body_b":"push_box","contact_count":1800.0,"contact_point_centroid":[0.51977,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":6.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49981,-0.03339,0.01465]}],"total_contact_groups":13},"final_pose_error":0.11687,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51977,0.05847,0.02499],"final_tcp_position":[0.50594,-0.03334,0.02153],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":141.97757,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":873.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":3492.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.50028,0.0578,0.03311],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07716,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.4348,-0.02857,0.16105],"tcp_start":[0.50028,0.0578,0.03311],"tcp_to_object_dist_end":0.15322,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":844.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3376.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49251,-0.12597,0.02699],"tcp_start":[0.4348,-0.02857,0.16105],"tcp_to_object_dist_end":0.10786,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53149,0.07286,0.03144],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.22516,"object_to_goal_dist_start":0.13127,"object_z_max":0.0316,"peak_contact_force":119.74511,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3097.0,"raw_peak_contact_force":141.97757,"tcp_end":[0.50542,0.04464,0.03004],"tcp_start":[0.49251,-0.12597,0.02699],"tcp_to_object_dist_end":0.03844,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":891.0,"n_steps_budget":1000.0,"object_pos_end":[0.56301,0.12589,0.03241],"object_pos_start":[0.53149,0.07286,0.03144],"object_to_goal_dist_end":0.2831,"object_to_goal_dist_start":0.22516,"object_z_max":0.03275,"peak_contact_force":31.90918,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2390.0,"raw_peak_contact_force":89.95841,"tcp_end":[0.52588,0.14495,0.02901],"tcp_start":[0.50542,0.04464,0.03004],"tcp_to_object_dist_end":0.04188,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51977,0.05847,0.02499],"object_pos_start":[0.56301,0.12589,0.03241],"object_to_goal_dist_end":0.2094,"object_to_goal_dist_start":0.2831,"object_z_max":0.03679,"peak_contact_force":0.24524,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2949.0,"raw_peak_contact_force":93.84884,"tcp_end":[0.50594,-0.03334,0.02153],"tcp_start":[0.52588,0.14495,0.02901],"tcp_to_object_dist_end":0.09291,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51977,0.05847,0.02499],"object_pos_start":[0.51977,0.05847,0.02499],"object_to_goal_dist_end":0.2094,"object_to_goal_dist_start":0.2094,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":1800.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.4987,-0.03334,0.01341],"tcp_start":[0.50594,-0.03334,0.02153],"tcp_to_object_dist_end":0.09491,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `589e611c6c27578474525e3fd29be4fb5907d8bbd5d1ca44922bfd811e342c78`; realized-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.51501,0.04767,0.025]}],"axes":[{"name":"push_direction","value":[-0.01501,-0.19767,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.51501,0.04767,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.53135,"average_solve_count":303.0,"average_success_count":303.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":-0.00797,"approach_2.speed":0.04291,"lift_1.lift_height":0.11602,"push_1.push_distance":0.17897,"push_1.push_speed":0.05772},"optimized_scores":{"best_composite_score":-0.05882,"best_fitness_score":0.34118,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":133.0,"contact_point_centroid":[0.54849,0.11576,0.06335],"force_p95":67.57574,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":85.77853,"mean_force":40.42808,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.51733,0.13842,0.03227]},{"body_a":"world","body_b":"push_box","contact_count":2150.0,"contact_point_centroid":[0.53495,0.10148,-0.00018],"force_p95":73.51497,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":85.11696,"mean_force":13.3769,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50861,0.02609,0.02389]},{"body_a":"world","body_b":"push_box","contact_count":1112.0,"contact_point_centroid":[0.55479,0.1247,-0.00012],"force_p95":50.862,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":82.13654,"mean_force":11.37147,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.51009,0.09991,0.03878]},{"body_a":"push_box","body_b":"link7","contact_count":574.0,"contact_point_centroid":[0.55288,0.11218,0.05579],"force_p95":74.44147,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":80.95131,"mean_force":46.1598,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51519,0.09799,0.02738]},{"body_a":"attachment","body_b":"push_box","contact_count":630.0,"contact_point_centroid":[0.52622,0.10589,0.0548],"force_p95":45.66971,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":64.51058,"mean_force":11.39441,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.5099,0.09903,0.03898]},{"body_a":"attachment","body_b":"push_box","contact_count":298.0,"contact_point_centroid":[0.54051,0.12448,0.06028],"force_p95":41.08588,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":50.84136,"mean_force":27.06402,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51683,0.12049,0.02832]},{"body_a":"attachment","body_b":"push_box","contact_count":170.0,"contact_point_centroid":[0.50784,0.03973,0.05119],"force_p95":26.81862,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.97237,"mean_force":12.35243,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50272,0.02795,0.04419]},{"body_a":"world","body_b":"push_box","contact_count":3461.0,"contact_point_centroid":[0.51575,0.05085,-1e-05],"force_p95":6.21343,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.26603,"mean_force":0.87305,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49587,-0.04981,0.03845]},{"body_a":"world","body_b":"push_box","contact_count":3960.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50423,0.06072,0.1639]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47617,0.06905,0.08765]},{"body_a":"world","body_b":"push_box","contact_count":3764.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46894,-0.05446,0.08417]},{"body_a":"world","body_b":"push_box","contact_count":1800.0,"contact_point_centroid":[0.51956,0.10203,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":6.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49704,-0.04156,0.01492]}],"total_contact_groups":12},"final_pose_error":0.10854,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51956,0.10203,0.02499],"final_tcp_position":[0.50316,-0.04155,0.02174],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":85.77853,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":990.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":3960.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.51027,0.12151,0.03099],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07424,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.44615,0.01783,0.14851],"tcp_start":[0.51027,0.12151,0.03099],"tcp_to_object_dist_end":0.14453,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":941.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3764.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49339,-0.12389,0.02549],"tcp_start":[0.44615,0.01783,0.14851],"tcp_to_object_dist_end":0.17291,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52237,0.07684,0.02798],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.22796,"object_to_goal_dist_start":0.19823,"object_z_max":0.02793,"peak_contact_force":0.18536,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3631.0,"raw_peak_contact_force":39.97237,"tcp_end":[0.50459,0.04507,0.04264],"tcp_start":[0.49339,-0.12389,0.02549],"tcp_to_object_dist_end":0.03925,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":759.0,"n_steps_budget":1000.0,"object_pos_end":[0.56042,0.14432,0.03119],"object_pos_start":[0.52237,0.07684,0.02798],"object_to_goal_dist_end":0.30052,"object_to_goal_dist_start":0.22796,"object_z_max":0.03214,"peak_contact_force":64.16785,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1875.0,"raw_peak_contact_force":85.77853,"tcp_end":[0.52049,0.14731,0.0299],"tcp_start":[0.50459,0.04507,0.04264],"tcp_to_object_dist_end":0.04006,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51956,0.10203,0.02499],"object_pos_start":[0.56042,0.14432,0.03119],"object_to_goal_dist_end":0.25278,"object_to_goal_dist_start":0.30052,"object_z_max":0.03701,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3022.0,"raw_peak_contact_force":85.11696,"tcp_end":[0.50316,-0.04155,0.02174],"tcp_start":[0.52049,0.14731,0.0299],"tcp_to_object_dist_end":0.14455,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51956,0.10203,0.02499],"object_pos_start":[0.51956,0.10203,0.02499],"object_to_goal_dist_end":0.25278,"object_to_goal_dist_start":0.25278,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":1800.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49594,-0.0415,0.01368],"tcp_start":[0.50316,-0.04155,0.02174],"tcp_to_object_dist_end":0.14589,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f2c9c63f0d9eca1b3ff8bf951759f6a3adee73f9f65e1cd3613c5e9d1203ebcc`; realized-scene SHA-256: `f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.47924,0.05847,0.025]}],"axes":[{"name":"push_direction","value":[0.02076,-0.20847,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.47924,0.05847,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.71053,"average_solve_count":304.0,"average_success_count":304.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":0.00652,"approach_2.speed":0.03465,"lift_1.lift_height":0.1351,"push_1.push_distance":0.19066,"push_1.push_speed":0.08645},"optimized_scores":{"best_composite_score":-0.07013,"best_fitness_score":0.32987,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":142.0,"contact_point_centroid":[0.48056,0.05062,0.04546],"force_p95":27.27054,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.12176,"mean_force":9.63906,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48057,0.03874,0.04493]},{"body_a":"attachment","body_b":"push_box","contact_count":339.0,"contact_point_centroid":[0.4714,0.11555,0.04161],"force_p95":15.44247,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.32641,"mean_force":6.19792,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.47446,0.10416,0.04029]},{"body_a":"world","body_b":"push_box","contact_count":3521.0,"contact_point_centroid":[0.47904,0.06118,-1e-05],"force_p95":1.1705,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.64046,"mean_force":0.64633,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48487,-0.04546,0.03916]},{"body_a":"world","body_b":"push_box","contact_count":1405.0,"contact_point_centroid":[0.45174,0.14569,-0.00012],"force_p95":7.76962,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.02096,"mean_force":1.8556,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.47423,0.11191,0.03827]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.42862,0.18168,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5443,"mean_force":0.24575,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47688,0.06417,0.02054]},{"body_a":"world","body_b":"push_box","contact_count":3972.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48715,0.06586,0.16416]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44808,0.07594,0.09006]},{"body_a":"world","body_b":"push_box","contact_count":3808.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4578,-0.054,0.08602]},{"body_a":"world","body_b":"push_box","contact_count":1800.0,"contact_point_centroid":[0.42862,0.18168,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":6.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47902,-0.02946,0.0139]}],"total_contact_groups":9},"final_pose_error":0.12162,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.42862,0.18168,0.02499],"final_tcp_position":[0.48501,-0.0294,0.02028],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":37.12176,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":993.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":3972.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.47614,0.13178,0.03157],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07366,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.42362,0.02089,0.15291],"tcp_start":[0.47614,0.13178,0.03157],"tcp_to_object_dist_end":0.14446,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":952.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3808.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49279,-0.12541,0.025],"tcp_start":[0.42362,0.02089,0.15291],"tcp_to_object_dist_end":0.18438,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4754,0.09363,0.02551],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.24487,"object_to_goal_dist_start":0.2095,"object_z_max":0.026,"peak_contact_force":0.13681,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3663.0,"raw_peak_contact_force":37.12176,"tcp_end":[0.47981,0.057,0.04291],"tcp_start":[0.49279,-0.12541,0.025],"tcp_to_object_dist_end":0.04079,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":693.0,"n_steps_budget":1000.0,"object_pos_end":[0.42882,0.18142,0.02472],"object_pos_start":[0.4754,0.09363,0.02551],"object_to_goal_dist_end":0.33898,"object_to_goal_dist_start":0.24487,"object_z_max":0.02572,"peak_contact_force":0.62768,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1744.0,"raw_peak_contact_force":25.32641,"tcp_end":[0.47194,0.16427,0.02499],"tcp_start":[0.47981,0.057,0.04291],"tcp_to_object_dist_end":0.04641,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.42862,0.18168,0.02499],"object_pos_start":[0.42882,0.18142,0.02472],"object_to_goal_dist_end":0.33928,"object_to_goal_dist_start":0.33898,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.5443,"tcp_end":[0.48501,-0.0294,0.02028],"tcp_start":[0.47194,0.16427,0.02499],"tcp_to_object_dist_end":0.21853,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.42862,0.18168,0.02499],"object_pos_start":[0.42862,0.18168,0.02499],"object_to_goal_dist_end":0.33928,"object_to_goal_dist_start":0.33928,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":1800.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.47793,-0.02942,0.01274],"tcp_start":[0.48501,-0.0294,0.02028],"tcp_to_object_dist_end":0.21714,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```