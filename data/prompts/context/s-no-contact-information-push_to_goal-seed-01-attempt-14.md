## Search State

- **Seed**: 1
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.2053 | 0.54 | ❌ rejected |
| 13 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.2081 | 0.55 | ✅ accepted |
| 12 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.2134 | 0.00 | ❌ rejected |
| 11 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.2048 | 0.54 | ❌ rejected |
| 10 | approach → push | linear_cartesian | impedance_motion | position_control | impedance_control | pose_tolerance | pose_tolerance | 2 | -0.0508 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.54 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `258b33ff0697721ed1ba4810cf28d81707440dffd73b12c632f307c6591915c0`
- Frozen object start: [0.5014185949640309, 0.05405564355911223, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.5014185949640309, 0.05405564355911223, 0.025)
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
  frozen_object_start: [0.5014, 0.0541, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.5014185949640309, 0.05405564355911223, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.0014, -0.2041, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 258b33ff0697721ed1ba4810cf28d81707440dffd73b12c632f307c6591915c0

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
| `object` | offset from object initial position (0.5014185949640309, 0.05405564355911223, 0.025) | approach/contact targets near object start |
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

## Current Skill (Q=0.205) — your mutation base

```yaml
skill: push_to_goal
phases:
- id: rotate_1
  type: rotate
  generator: impedance_motion
  control: impedance_control
  termination: time_limit
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01
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
- id: align_2
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01

```

## Design Metrics

- **Composite score**: 0.205
- **task_score** (E): 0.540
- **fitness_score**: 0.415  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| rotate_1 | 1.00 | 0.1849 |
| align_1 | 1.00 | 0.1928 |
| push_1 | 0.67 | 0.1684 |
| align_2 | 1.00 | 0.0634 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| rotate_1 | rotate | 1.00 / time_limit | (0.500, -0.000, 0.301)→(0.497, -0.086, 0.137) | (0.474, -0.001, 0.025)→(0.474, -0.001, 0.025) | 0.154→0.154 |
| align_1 | align | 1.00 / step_budget | (0.497, -0.086, 0.137)→(0.473, 0.069, 0.030) | (0.474, -0.001, 0.025)→(0.475, 0.009, 0.028) | 0.154→0.163 |
| push_1 | push | 0.67 / step_budget | (0.473, 0.069, 0.030)→(0.495, -0.097, 0.022) | (0.475, 0.009, 0.028)→(0.472, -0.112, 0.028) | 0.163→0.056 |
| align_2 | align | 1.00 / step_budget | (0.495, -0.097, 0.022)→(0.470, -0.039, 0.023) | (0.472, -0.112, 0.028)→(0.463, -0.100, 0.025) | 0.056→0.070 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- approach_alignment: 0.641
- goal_progress: 0.927
- terminal_score: 0.927
- phase_score: 0.424
- phase_breakdown.push_score: 0.825
- phase_breakdown.approach_score: 0.056

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.625
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.927
- **Median Q (composite search score)**: 0.120
- **K-run variance**: 0.0223
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.265


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `f21cc79f03d9e871b86947069440973ee7e2ef557ebaac0b26b4f6cbdabf5bb1`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `ec03d65db90cc6b4602194a1eefa4c3104517a971e566e099fb50a3df7102251`; realized-scene SHA-256: `258b33ff0697721ed1ba4810cf28d81707440dffd73b12c632f307c6591915c0`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50142,0.05406,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.00142,-0.20406,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.50142,0.05406,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.78767,"average_solve_count":146.0,"average_success_count":146.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00907,"align_2.lateral_offset_x":0.00548,"push_1.push_distance":0.19333},"optimized_scores":{"best_composite_score":0.08025,"best_fitness_score":0.29025,"best_task_score":0.56625},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":286.0,"contact_point_centroid":[0.51033,0.08541,0.04646],"force_p95":154.66051,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":181.6215,"mean_force":112.54583,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50235,0.09183,0.04903]},{"body_a":"world","body_b":"push_box","contact_count":3422.0,"contact_point_centroid":[0.50174,0.05825,-9e-05],"force_p95":81.58625,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":164.76933,"mean_force":9.73416,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49612,0.00715,0.08615]},{"body_a":"attachment","body_b":"push_box","contact_count":994.0,"contact_point_centroid":[0.50373,0.0323,0.03086],"force_p95":74.71531,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":79.94346,"mean_force":54.46107,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5017,0.04357,0.03147]},{"body_a":"world","body_b":"push_box","contact_count":1913.0,"contact_point_centroid":[0.49656,-0.00305,-0.00016],"force_p95":58.71652,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":72.33441,"mean_force":40.17515,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50174,0.04632,0.03163]},{"body_a":"push_box","body_b":"link7","contact_count":1000.0,"contact_point_centroid":[0.52172,0.00895,0.06802],"force_p95":31.4085,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":53.8641,"mean_force":28.81612,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5017,0.04403,0.03148]},{"body_a":"push_box","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.52838,0.09012,0.06853],"force_p95":39.95326,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.31824,"mean_force":36.49581,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50206,0.12188,0.0353]},{"body_a":"world","body_b":"push_box","contact_count":323.0,"contact_point_centroid":[0.47114,-0.07259,-0.00025],"force_p95":17.22334,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.08926,"mean_force":3.7713,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.48759,-0.02108,0.02608]},{"body_a":"push_box","body_b":"link7","contact_count":105.0,"contact_point_centroid":[0.50498,-0.06984,0.06617],"force_p95":23.51392,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.3069,"mean_force":9.90002,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49413,-0.03361,0.02509]},{"body_a":"attachment","body_b":"push_box","contact_count":10.0,"contact_point_centroid":[0.49842,-0.05404,0.0258],"force_p95":2.95696,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.01297,"mean_force":0.65125,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49913,-0.04223,0.0254]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49729,-0.0436,0.21555]}],"total_contact_groups":10},"final_pose_error":0.00995,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47916,-0.06398,0.02487],"final_tcp_position":[0.48189,-0.00951,0.02744],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"phases":[{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","tcp_end":[0.4966,-0.08596,0.13695],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.17934,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50341,0.08175,0.03419],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.23196,"object_to_goal_dist_start":0.20406,"object_z_max":0.03486,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","tcp_end":[0.50193,0.12221,0.03486],"tcp_start":[0.4966,-0.08596,0.13695],"tcp_to_object_dist_end":0.04049,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48258,-0.08166,0.03352],"object_pos_start":[0.50341,0.08175,0.03419],"object_to_goal_dist_end":0.07103,"object_to_goal_dist_start":0.23196,"object_z_max":0.0343,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","tcp_end":[0.49938,-0.04209,0.02549],"tcp_start":[0.50193,0.12221,0.03486],"tcp_to_object_dist_end":0.04374,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":189.0,"n_steps_budget":600.0,"object_pos_end":[0.47916,-0.06398,0.02487],"object_pos_start":[0.48258,-0.08166,0.03352],"object_to_goal_dist_end":0.08851,"object_to_goal_dist_start":0.07103,"object_z_max":0.03352,"phase_name":"align_2","phase_peak_obstacle_force":0.0,"phase_type":"align","tcp_end":[0.48189,-0.00951,0.02744],"tcp_start":[0.49938,-0.04209,0.02549],"tcp_to_object_dist_end":0.0546,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `060d405a872aae8d4597ed6284dedb60e9c99f80071c0520b1a8a2986f3c114d`; realized-scene SHA-256: `8c36a5f9300ba3a57ccc09620ec8ba0a5276276ed83fb4303679e150911bfa14`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47139,-0.02418,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02861,-0.12582,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47139,-0.02418,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.77037,"average_solve_count":135.0,"average_success_count":135.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00948,"align_2.lateral_offset_x":0.00208,"push_1.push_distance":0.12707},"optimized_scores":{"best_composite_score":0.41516,"best_fitness_score":0.62516,"best_task_score":0.92711},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":115.0,"contact_point_centroid":[0.52177,-0.15182,0.05258],"force_p95":35.19091,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.73113,"mean_force":26.1429,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49166,-0.11304,0.01983]},{"body_a":"world","body_b":"push_box","contact_count":552.0,"contact_point_centroid":[0.49624,-0.14751,-0.00019],"force_p95":31.93474,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":34.08838,"mean_force":5.85034,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49178,-0.10317,0.01969]},{"body_a":"attachment","body_b":"push_box","contact_count":751.0,"contact_point_centroid":[0.48569,-0.06828,0.03057],"force_p95":17.24441,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.20124,"mean_force":4.49628,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48118,-0.0563,0.0216]},{"body_a":"world","body_b":"push_box","contact_count":2069.0,"contact_point_centroid":[0.4792,-0.07481,-4e-05],"force_p95":7.45084,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.96111,"mean_force":1.92345,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47697,-0.02767,0.02239]},{"body_a":"push_box","body_b":"link7","contact_count":10.0,"contact_point_centroid":[0.52156,-0.13329,0.05035],"force_p95":5.63382,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.22634,"mean_force":1.25024,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49094,-0.11793,0.02054]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49729,-0.0436,0.21555]},{"body_a":"world","body_b":"push_box","contact_count":2520.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48142,-0.0196,0.08025]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.50569,-0.13542,0.05],"force_p95":0.0,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49172,-0.12335,0.0204]}],"total_contact_groups":8},"final_pose_error":0.00996,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49573,-0.15838,0.02494],"final_tcp_position":[0.49215,-0.08701,0.01969],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"phases":[{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","tcp_end":[0.4966,-0.08596,0.13695],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.13033,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":630.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","tcp_end":[0.46892,0.04665,0.02746],"tcp_start":[0.4966,-0.08596,0.13695],"tcp_to_object_dist_end":0.07092,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49699,-0.1602,0.02511],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.01063,"object_to_goal_dist_start":0.12903,"object_z_max":0.0254,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","tcp_end":[0.49175,-0.12325,0.02043],"tcp_start":[0.46892,0.04665,0.02746],"tcp_to_object_dist_end":0.03761,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":215.0,"n_steps_budget":600.0,"object_pos_end":[0.49573,-0.15838,0.02494],"object_pos_start":[0.49699,-0.1602,0.02511],"object_to_goal_dist_end":0.0094,"object_to_goal_dist_start":0.01063,"object_z_max":0.02929,"phase_name":"align_2","phase_peak_obstacle_force":0.0,"phase_type":"align","tcp_end":[0.49215,-0.08701,0.01969],"tcp_start":[0.49175,-0.12325,0.02043],"tcp_to_object_dist_end":0.07165,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `c4af277909bfbef2010e50829d2192ea184fe34d7420833f45dd73455a81c9b6`; realized-scene SHA-256: `35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45028,-0.03158,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.04972,-0.11842,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.45028,-0.03158,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91489,"average_solve_count":141.0,"average_success_count":141.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00147,"align_2.lateral_offset_x":0.0013,"push_1.push_distance":0.10472},"optimized_scores":{"best_composite_score":0.12044,"best_fitness_score":0.33044,"best_task_score":0.12742},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":339.0,"contact_point_centroid":[0.46341,-0.04418,0.02439],"force_p95":14.9938,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.65364,"mean_force":3.90751,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46637,-0.03304,0.02262]},{"body_a":"attachment","body_b":"push_box","contact_count":74.0,"contact_point_centroid":[0.45873,-0.07783,0.02283],"force_p95":12.6973,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.63348,"mean_force":6.00258,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.46773,-0.08256,0.01763]},{"body_a":"world","body_b":"push_box","contact_count":1585.0,"contact_point_centroid":[0.42257,-0.08451,-3e-05],"force_p95":2.70743,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.87042,"mean_force":0.55692,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.46218,-0.07116,0.01864]},{"body_a":"world","body_b":"push_box","contact_count":2989.0,"contact_point_centroid":[0.44135,-0.06897,-3e-05],"force_p95":3.50104,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.7553,"mean_force":0.7141,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47081,-0.04786,0.02241]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49729,-0.0436,0.21555]},{"body_a":"world","body_b":"push_box","contact_count":2388.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.47184,-0.02372,0.08098]}],"total_contact_groups":6},"final_pose_error":0.00991,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.41389,-0.07828,0.02499],"final_tcp_position":[0.43656,-0.02156,0.0206],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"phases":[{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","tcp_end":[0.4966,-0.08596,0.13695],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.13281,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":597.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","tcp_end":[0.44945,0.03913,0.0283],"tcp_start":[0.4966,-0.08596,0.13695],"tcp_to_object_dist_end":0.07079,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.43589,-0.0927,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.08599,"object_to_goal_dist_start":0.12843,"object_z_max":0.02533,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","tcp_end":[0.49247,-0.12423,0.02018],"tcp_start":[0.44945,0.03913,0.0283],"tcp_to_object_dist_end":0.06495,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":481.0,"n_steps_budget":810.0,"object_pos_end":[0.41389,-0.07828,0.02499],"object_pos_start":[0.43589,-0.0927,0.02499],"object_to_goal_dist_end":0.11207,"object_to_goal_dist_start":0.08599,"object_z_max":0.02519,"phase_name":"align_2","phase_peak_obstacle_force":0.0,"phase_type":"align","tcp_end":[0.43656,-0.02156,0.0206],"tcp_start":[0.49247,-0.12423,0.02018],"tcp_to_object_dist_end":0.06124,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```