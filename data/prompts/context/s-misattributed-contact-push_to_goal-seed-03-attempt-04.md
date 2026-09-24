## Search State

- **Seed**: 3
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1516 | 0.37 | ❌ rejected |
| 3 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1522 | 0.37 | ❌ rejected |
| 2 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1523 | 0.37 | ✅ accepted |
| 1 | rotate → retract → descend → pull | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | -0.2100 | 0.00 | ❌ rejected |
| 0 | rotate → retract → descend → pull | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | -0.2100 | 0.00 | ✅ accepted |

**Proposal policy**: task_score is 0.37 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be`
- Frozen object start: [0.45027790005723495, -0.03158273920846803, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.45027790005723495, -0.03158273920846803, 0.025)
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
  frozen_object_start: [0.4503, -0.0316, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.45027790005723495, -0.03158273920846803, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [0.0497, -0.1184, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be

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
| `object` | offset from object initial position (0.45027790005723495, -0.03158273920846803, 0.025) | approach/contact targets near object start |
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

## Current Skill (Q=0.152) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.4
- id: push_to_goal
  target_entity: object
  metric: goal_progress
  weight: 0.6
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.02
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: generator.speed
        mode: add
  subtask_id: reach_object
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.01
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: add
  subtask_id: reach_object
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.15
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: positive
    tolerance: 0.05
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  guards:
  - id: contact_ok
    when: during_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.005
  subtask_id: push_to_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (add)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (add)
- **push_1** (`push`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.15, mode=replace_offset_projection, sign=positive}, tolerance=0.05
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
  - guards:
    - id=contact_ok, when=during_phase, predicate=contact_detected, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.005]

## Design Metrics

- **Composite score**: 0.152
- **task_score** (E): 0.370
- **fitness_score**: 0.332  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.180

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1646 |
| descend_1 | 1.00 | 1.00 | 0.0968 |
| push_1 | 1.00 | 1.00 | 0.1385 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.509, 0.002, 0.143) | (0.513, 0.002, 0.025)→(0.513, 0.002, 0.025) | 0.160→0.160 | 1.00 / 5.000 | 252.450 | 275.925 |
| descend_1 | descend | 1.00 / step_budget | (0.509, 0.002, 0.143)→(0.523, 0.002, 0.047) | (0.513, 0.002, 0.025)→(0.517, 0.002, 0.024) | 0.160→0.160 | 1.00 / 2.333 | 0.683 | 241.692 |
| push_1 | push | 1.00 / step_budget | (0.523, 0.002, 0.047)→(0.509, -0.128, 0.029) | (0.517, 0.002, 0.024)→(0.528, -0.052, 0.028) | 0.160→0.103 | 1.00 / 4.000 | 0.245 | 0.245 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.628
- lateral_force_integral: None
- approach_alignment: 0.736
- goal_progress: 0.521
- terminal_score: 0.521
- phase_score: 0.393
- phase_breakdown.push_to_goal_score: 0.515
- phase_breakdown.reach_object_score: 0.211

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.444
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.521
- **Median Q (composite search score)**: 0.113
- **K-run variance**: 0.0065
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.524


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `01fea9f27a58d64b0f9b0ff0cae1096a52b0da1ad311c77058a75ddb9aab77d2`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `c53c9bf1992485fcf877d50f4ee23d3483b4b9e63e5a19adda2461c26d89c46e`; realized-scene SHA-256: `35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45028,-0.03158,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.04972,-0.11842,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.45028,-0.03158,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.12821,"average_solve_count":78.0,"average_success_count":78.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.33716,"descend_1.descend_speed":0.12756,"push_1.push_distance":0.18622},"optimized_scores":{"best_composite_score":0.26431,"best_fitness_score":0.44431,"best_task_score":0.52117},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":104.0,"contact_point_centroid":[0.46463,-0.03116,0.04632],"force_p95":291.07225,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":298.91452,"mean_force":249.86723,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45426,-0.03094,0.05031]},{"body_a":"attachment","body_b":"push_box","contact_count":89.0,"contact_point_centroid":[0.486,-0.05109,0.04748],"force_p95":273.10239,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":275.57776,"mean_force":173.4281,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48045,-0.05888,0.04856]},{"body_a":"world","body_b":"push_box","contact_count":178.0,"contact_point_centroid":[0.48668,-0.06031,-0.00124],"force_p95":243.96816,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":258.57222,"mean_force":87.76496,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48476,-0.07908,0.04392]},{"body_a":"world","body_b":"push_box","contact_count":1524.0,"contact_point_centroid":[0.45056,-0.03163,-0.00015],"force_p95":130.67656,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":153.14428,"mean_force":17.38865,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45126,-0.02935,0.08626]},{"body_a":"world","body_b":"push_box","contact_count":1160.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24532,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47735,-0.01327,0.22291]}],"total_contact_groups":5},"final_pose_error":0.04941,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50537,-0.08959,0.03517],"final_tcp_position":[0.50708,-0.15829,0.02844],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":298.91452,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":290.0,"n_steps_budget":600.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":274.98298,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1628.0,"raw_peak_contact_force":298.91452,"subtask_id":"reach_object","tcp_end":[0.45437,-0.02737,0.14379],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.11895,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":381.0,"n_steps_budget":600.0,"object_pos_end":[0.45394,-0.03196,0.02359],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12672,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":0.72432,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":267.0,"raw_peak_contact_force":275.57776,"subtask_id":"reach_object","tcp_end":[0.462,-0.03175,0.048],"tcp_start":[0.45437,-0.02737,0.14379],"tcp_to_object_dist_end":0.02571,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":151.0,"n_steps_budget":1000.0,"object_pos_end":[0.50537,-0.08959,0.03517],"object_pos_start":[0.45394,-0.03196,0.02359],"object_to_goal_dist_end":0.0615,"object_to_goal_dist_start":0.12672,"object_z_max":0.03867,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1160.0,"raw_peak_contact_force":0.24534,"subtask_id":"push_to_goal","tcp_end":[0.50708,-0.15829,0.02844],"tcp_start":[0.462,-0.03175,0.048],"tcp_to_object_dist_end":0.06906,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `234a0edc218dcf63b67654ddcfd8b0f12da84040687f62c4c4845001a50f549a`; realized-scene SHA-256: `721a00290a47301d7751e432f1a041db545f1b55cfdb74b1d642c32f5b25f702`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.55317,0.00136,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.05317,-0.15136,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.55317,0.00136,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.11494,"average_solve_count":87.0,"average_success_count":87.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.47909,"descend_1.descend_speed":0.16912,"push_1.push_distance":0.22493},"optimized_scores":{"best_composite_score":0.11251,"best_fitness_score":0.29251,"best_task_score":0.3165},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":97.0,"contact_point_centroid":[0.56532,0.00126,0.04698],"force_p95":252.14337,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":261.46723,"mean_force":214.75213,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.55384,0.00121,0.04884]},{"body_a":"attachment","body_b":"push_box","contact_count":94.0,"contact_point_centroid":[0.56715,-0.01804,0.04978],"force_p95":209.20682,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":212.18706,"mean_force":164.21839,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.55925,-0.02485,0.05069]},{"body_a":"world","body_b":"push_box","contact_count":471.0,"contact_point_centroid":[0.55205,-0.03798,-0.00059],"force_p95":142.95784,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":152.60806,"mean_force":33.23927,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53398,-0.07884,0.04024]},{"body_a":"world","body_b":"push_box","contact_count":1440.0,"contact_point_centroid":[0.55364,0.00136,-0.00012],"force_p95":109.38365,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":131.50678,"mean_force":14.80003,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.54649,0.00114,0.08441]},{"body_a":"world","body_b":"push_box","contact_count":1200.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52089,0.00054,0.22213]}],"total_contact_groups":5},"final_pose_error":0.04933,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.54989,-0.05236,0.02484],"final_tcp_position":[0.49539,-0.16289,0.02577],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":261.46723,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":300.0,"n_steps_budget":600.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":238.94155,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1537.0,"raw_peak_contact_force":261.46723,"subtask_id":"reach_object","tcp_end":[0.54368,0.00111,0.14212],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.11752,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":361.0,"n_steps_budget":600.0,"object_pos_end":[0.55747,0.00137,0.02378],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16191,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":0.24307,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":565.0,"raw_peak_contact_force":212.18706,"subtask_id":"reach_object","tcp_end":[0.56186,0.00124,0.04676],"tcp_start":[0.54368,0.00111,0.14212],"tcp_to_object_dist_end":0.0234,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":202.0,"n_steps_budget":1000.0,"object_pos_end":[0.54989,-0.05236,0.02484],"object_pos_start":[0.55747,0.00137,0.02378],"object_to_goal_dist_end":0.10965,"object_to_goal_dist_start":0.16191,"object_z_max":0.03515,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1200.0,"raw_peak_contact_force":0.24534,"subtask_id":"push_to_goal","tcp_end":[0.49539,-0.16289,0.02577],"tcp_start":[0.56186,0.00124,0.04676],"tcp_to_object_dist_end":0.12324,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `107d1233d3b0a09f0fa34aa18231b315c9a1d92237bb254399d486ed8004836a`; realized-scene SHA-256: `b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5366,0.03695,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.0366,-0.18695,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5366,0.03695,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.13889,"average_solve_count":72.0,"average_success_count":72.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.33773,"descend_1.descend_speed":0.17037,"push_1.push_distance":0.14831},"optimized_scores":{"best_composite_score":0.0781,"best_fitness_score":0.2581,"best_task_score":0.27185},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":98.0,"contact_point_centroid":[0.54915,0.0359,0.04689],"force_p95":256.86631,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":267.39192,"mean_force":219.16359,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53781,0.03591,0.04912]},{"body_a":"attachment","body_b":"push_box","contact_count":101.0,"contact_point_centroid":[0.55276,0.01393,0.04819],"force_p95":232.89113,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":237.31107,"mean_force":172.16253,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.54498,0.0073,0.04924]},{"body_a":"world","body_b":"push_box","contact_count":239.0,"contact_point_centroid":[0.53877,0.01322,-0.0008],"force_p95":181.77177,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":185.60189,"mean_force":73.34341,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.54393,0.00712,0.04806]},{"body_a":"world","body_b":"push_box","contact_count":1454.0,"contact_point_centroid":[0.537,0.037,-0.00012],"force_p95":112.58869,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":136.04384,"mean_force":15.1112,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53111,0.0341,0.08487]},{"body_a":"world","body_b":"push_box","contact_count":1188.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24532,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51377,0.01547,0.22245]}],"total_contact_groups":5},"final_pose_error":0.04923,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52997,-0.01457,0.02363],"final_tcp_position":[0.5247,-0.06167,0.03319],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":267.39192,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":297.0,"n_steps_budget":600.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":243.42653,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1552.0,"raw_peak_contact_force":267.39192,"subtask_id":"reach_object","tcp_end":[0.52918,0.03191,0.14268],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.11803,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":364.0,"n_steps_budget":600.0,"object_pos_end":[0.54069,0.03731,0.02376],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.19169,"object_to_goal_dist_start":0.1905,"object_z_max":0.02499,"peak_contact_force":1.08074,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":340.0,"raw_peak_contact_force":237.31107,"subtask_id":"reach_object","tcp_end":[0.54581,0.03672,0.04699],"tcp_start":[0.52918,0.03191,0.14268],"tcp_to_object_dist_end":0.02379,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":128.0,"n_steps_budget":960.0,"object_pos_end":[0.52997,-0.01457,0.02363],"object_pos_start":[0.54069,0.03731,0.02376],"object_to_goal_dist_end":0.13871,"object_to_goal_dist_start":0.19169,"object_z_max":0.03475,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1188.0,"raw_peak_contact_force":0.24534,"subtask_id":"push_to_goal","tcp_end":[0.5247,-0.06167,0.03319],"tcp_start":[0.54581,0.03672,0.04699],"tcp_to_object_dist_end":0.04835,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```